// files4testing Go harness.
//
// Run your own decompressor against every test vector:
//
//	go run ./harness_go            # full suite
//	SKIP_COMBINATION=1 go run ./harness_go
//
// The harness reads manifest.json, calls decompress(entry, input), and
// asserts sha256(output) == entry.expected_sha256.
//
// Implement decompress() below with your own logic. The default shell-based
// implementation is a working reference that proves the harness end-to-end.
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

type RawFile struct {
	Path   string `json:"path"`
	Size   uint64 `json:"size"`
	SHA256 string `json:"sha256"`
}

type Entry struct {
	Layer         string `json:"layer"`
	Kind          string `json:"kind"`
	Path          string `json:"path"`
	Format        string `json:"format"`
	Level         string `json:"level"`
	IsArchive     bool   `json:"is_archive"`
	IsVolume      bool   `json:"is_volume"`
	VolumeCount   *int   `json:"volume_count"`
	Password      string `json:"password"`
	ExpectedFile  string `json:"expected_file"`
	ExpectedSize  uint64 `json:"expected_size"`
	ExpectedSHA   string `json:"expected_sha256"`
}

type Manifest struct {
	RawFiles map[string]RawFile `json:"raw_files"`
	Entries  []Entry            `json:"entries"`
}

var rootDir string

// ===========================================================================
// Implement your decompressor here.
// ===========================================================================

// decompress returns the decompressed bytes for entry, or an error on failure.
func decompress(entry Entry) ([]byte, error) {
	path := filepath.Join(rootDir, entry.Path)
	args := []string{}
	var name string

	switch entry.Format {
	case "gzip", "bzip2", "xz", "lzma", "lz4", "zstd", "brotli":
		name, args = entry.Format, []string{"-dc", path}
	case "zip":
		name = "unzip"
		if entry.Password != "" {
			args = []string{"-P", entry.Password, "-p", path}
		} else {
			args = []string{"-p", path}
		}
	case "7z":
		name = "7z"
		if entry.Password != "" {
			args = []string{"x", "-so", "-y", "-p" + entry.Password, path}
		} else {
			args = []string{"x", "-so", "-y", path}
		}
	case "rar":
		name = "unrar"
		if entry.Password != "" {
			args = []string{"p", "-inul", "-p" + entry.Password, path}
		} else {
			args = []string{"p", "-inul", path}
		}
	default:
		return nil, fmt.Errorf("unsupported format: %s", entry.Format)
	}

	cmd := exec.Command(name, args...)
	out, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("%s failed: %v: %s", name, err, out[:min(len(out), 200)])
	}
	return out, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// ===========================================================================
// End of user implementation.
// ===========================================================================

func sha256Hex(data []byte) string {
	h := sha256.Sum256(data)
	return hex.EncodeToString(h[:])
}

func main() {
	_, err := exec.LookPath("unrar")
	if err != nil && runtime.GOOS == "darwin" {
		fmt.Println("note: unrar not found; rar cases will fail")
	}

	// rootDir = parent of this package dir (repo root)
	dir, _ := os.Getwd()
	for {
		if _, err := os.Stat(filepath.Join(dir, "manifest.json")); err == nil {
			rootDir = dir
			break
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			fmt.Fprintln(os.Stderr, "manifest.json not found; run from repo root or harness_go/")
			os.Exit(1)
		}
		dir = parent
	}

	data, err := os.ReadFile(filepath.Join(rootDir, "manifest.json"))
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var m Manifest
	if err := json.Unmarshal(data, &m); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	skipBig := os.Getenv("SKIP_COMBINATION") == "1"
	pass, fail := 0, 0
	for _, e := range m.Entries {
		if skipBig && e.Kind == "combination" {
			fmt.Printf("[skip] %s\n", e.Path)
			continue
		}
		out, err := decompress(e)
		if err != nil {
			fmt.Printf("[error] %s: %v\n", e.Path, err)
			fail++
			continue
		}
		got := sha256Hex(out)
		if got == e.ExpectedSHA {
			fmt.Printf("[ok] %s (%s/%s) %s\n", e.Path, e.Format, e.Level, got)
			pass++
		} else {
			fmt.Printf("[MISMATCH] %s (%s/%s) got %s want %s\n", e.Path, e.Format, e.Level, got, e.ExpectedSHA)
			fail++
		}
	}

	fmt.Printf("\nPASS: %d  FAIL: %d\n", pass, fail)
	if fail > 0 {
		os.Exit(1)
	}
	fmt.Println("All test vectors verified OK.")
}
