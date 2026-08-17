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
	"sort"
	"strings"
)

type RawFile struct {
	Path   string `json:"path"`
	Size   uint64 `json:"size"`
	SHA256 string `json:"sha256"`
}

type FileExpect struct {
	Path   string `json:"path"`
	Size   uint64 `json:"size"`
	SHA256 string `json:"sha256"`
}

type Entry struct {
	Layer         string       `json:"layer"`
	Kind          string       `json:"kind"`
	Path          string       `json:"path"`
	Format        string       `json:"format"`
	Level         string       `json:"level"`
	IsArchive     bool         `json:"is_archive"`
	IsVolume      bool         `json:"is_volume"`
	VolumeCount   *int         `json:"volume_count"`
	Password      string       `json:"password"`
	ExpectedFile  string       `json:"expected_file"`
	ExpectedSize  uint64       `json:"expected_size"`
	ExpectedSHA   string       `json:"expected_sha256"`
	ExpectedFiles []FileExpect `json:"expected_files"`
	TreeSHA       string       `json:"tree_sha256"`
	Note          string       `json:"note"`
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
		out, err := exec.Command(name, args...).CombinedOutput()
		if err == nil {
			return out, nil
		}
		// unzip may not support exotic methods / byte-volumes; fall back to 7z
		name = "7z"
		if entry.Password != "" {
			args = []string{"x", "-so", "-y", "-p" + entry.Password, path}
		} else {
			args = []string{"x", "-so", "-y", path}
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
	case "iso":
		name, args = "7z", []string{"x", "-so", "-y", path}
	case "tar":
		name = "tar"
		args = []string{"-xOf", path, filepath.Base(entry.ExpectedFile)}
	default:
		if strings.HasPrefix(entry.Format, "tar.") {
			inner := strings.TrimPrefix(entry.Format, "tar.")
			tools := map[string]string{
				"gzip": "gzip", "bzip2": "bzip2", "xz": "xz",
				"lzma": "lzma", "lz4": "lz4", "zstd": "zstd", "brotli": "brotli",
			}
			tn, ok := tools[inner]
			if !ok {
				return nil, fmt.Errorf("unsupported tar inner: %s", inner)
			}
			stream, err := exec.Command(tn, "-dc", path).Output()
			if err != nil {
				return nil, fmt.Errorf("%s failed: %v", tn, err)
			}
			tmp, err := os.CreateTemp("", "tarstream-*")
			if err != nil {
				return nil, err
			}
			tmpName := tmp.Name()
			if _, err := tmp.Write(stream); err != nil {
				tmp.Close()
				os.Remove(tmpName)
				return nil, err
			}
			tmp.Close()
			out, err := exec.Command("tar", "-xOf", tmpName, filepath.Base(entry.ExpectedFile)).Output()
			os.Remove(tmpName)
			if err != nil {
				return nil, fmt.Errorf("tar failed: %v", err)
			}
			return out, nil
		}
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

// decompressTree extracts a multi-file / tree entry into outDir using
// reference tools (mirroring verify.sh). Implement your own when you support
// tree extraction natively.
func decompressTree(e Entry, outDir string) error {
	path := filepath.Join(rootDir, e.Path)
	var name string
	args := []string{}
	switch e.Format {
	case "iso":
		name, args = "7z", []string{"x", "-y", "-o" + outDir, path}
	case "tar":
		name, args = "tar", []string{"-xf", path, "-C", outDir}
	case "zip":
		name = "unzip"
		if e.Password != "" {
			args = []string{"-o", "-q", "-P", e.Password, path, "-d", outDir}
		} else {
			args = []string{"-o", "-q", path, "-d", outDir}
		}
	case "7z":
		name = "7z"
		if e.Password != "" {
			args = []string{"x", "-y", "-o" + outDir, "-p" + e.Password, path}
		} else {
			args = []string{"x", "-y", "-o" + outDir, path}
		}
	case "rar":
		name = "unrar"
		if e.Password != "" {
			args = []string{"x", "-inul", "-p" + e.Password, path, outDir + "/"}
		} else {
			args = []string{"x", "-inul", path, outDir + "/"}
		}
	default:
		if strings.HasPrefix(e.Format, "tar.") {
			inner := strings.TrimPrefix(e.Format, "tar.")
			tools := map[string]string{
				"gzip": "gzip", "bzip2": "bzip2", "xz": "xz",
				"lzma": "lzma", "lz4": "lz4", "zstd": "zstd", "brotli": "brotli",
			}
			tn, ok := tools[inner]
			if !ok {
				return fmt.Errorf("unsupported tar inner: %s", inner)
			}
			stream, err := exec.Command(tn, "-dc", path).Output()
			if err != nil {
				return fmt.Errorf("%s failed: %v", tn, err)
			}
			tmp, err := os.CreateTemp("", "tarstream-*")
			if err != nil {
				return err
			}
			tmpName := tmp.Name()
			if _, err := tmp.Write(stream); err != nil {
				tmp.Close()
				os.Remove(tmpName)
				return err
			}
			tmp.Close()
			out, err := exec.Command("tar", "-xf", tmpName, "-C", outDir).CombinedOutput()
			os.Remove(tmpName)
			if err != nil {
				return fmt.Errorf("tar failed: %v: %s", err, out)
			}
			return nil
		}
		return fmt.Errorf("no tree extractor for format: %s", e.Format)
	}
	out, err := exec.Command(name, args...).CombinedOutput()
	if err != nil {
		return fmt.Errorf("%s failed: %v: %s", name, err, out[:min(len(out), 200)])
	}
	return nil
}

// checkTree asserts every expected file's sha256 and the whole-tree hash.
func checkTree(outDir string, e Entry) error {
	for _, ef := range e.ExpectedFiles {
		fp := filepath.Join(outDir, filepath.FromSlash(ef.Path))
		data, err := os.ReadFile(fp)
		if err != nil {
			return fmt.Errorf("tree member missing: %s", ef.Path)
		}
		if sha256Hex(data) != ef.SHA256 {
			return fmt.Errorf("tree member mismatch: %s", ef.Path)
		}
	}
	h := sha256.New()
	efs := append([]FileExpect(nil), e.ExpectedFiles...)
	sort.Slice(efs, func(i, j int) bool { return efs[i].Path < efs[j].Path })
	for _, ef := range efs {
		h.Write([]byte(ef.Path))
		h.Write([]byte{0})
		data, err := os.ReadFile(filepath.Join(outDir, filepath.FromSlash(ef.Path)))
		if err != nil {
			return err
		}
		h.Write(data)
	}
	if hex.EncodeToString(h.Sum(nil)) != e.TreeSHA {
		return fmt.Errorf("tree hash mismatch")
	}
	return nil
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

	if _, err := os.Stat(filepath.Join(rootDir, "normal")); err != nil {
		fmt.Fprintln(os.Stderr, "Data not found. Compressed files are hosted in the GitHub Release — download the tarballs and extract them into the repo root first. See README.md")
		os.Exit(2)
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
		if e.Format == "cso" {
			fmt.Printf("[skip] %s (cso: no reference CLI)\n", e.Path)
			continue
		}
		if len(e.ExpectedFiles) > 0 {
			// tree entry: extract to a temp dir and assert files + tree hash
			outDir, err := os.MkdirTemp("", "uu_harness_tree_")
			if err != nil {
				fmt.Printf("[error] %s: %v\n", e.Path, err)
				fail++
				continue
			}
			err = decompressTree(e, outDir)
			if err == nil {
				err = checkTree(outDir, e)
			}
			os.RemoveAll(outDir)
			if err != nil {
				fmt.Printf("[error] %s: %v\n", e.Path, err)
				fail++
				continue
			}
			fmt.Printf("[ok] %s (%s/%s) tree\n", e.Path, e.Format, e.Level)
			pass++
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
