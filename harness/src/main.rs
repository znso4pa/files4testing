//! files4testing harness — run your own decompressor against every test vector.
//!
//! README: implement `Decompressor` below, then run:
//!   cargo run --release
//!
//! The harness reads `manifest.json`, feeds each compressed file to your
//! decompressor, and asserts that the output's SHA-256 matches the expected
//! value recorded when the dataset was built.

use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::error::Error;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct RawFile {
    path: String,
    size: u64,
    sha256: String,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct Entry {
    layer: String,
    kind: String,
    path: String,
    format: String,
    level: String,
    is_archive: bool,
    is_volume: bool,
    volume_count: Option<usize>,
    password: Option<String>,
    expected_file: String,
    expected_size: u64,
    expected_sha256: String,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct Manifest {
    raw_files: std::collections::HashMap<String, RawFile>,
    entries: Vec<Entry>,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct FaultEntry {
    path: String,
    format: String,
    reason: String,
    password: Option<String>,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct FaultManifest {
    entries: Vec<FaultEntry>,
}

// ===========================================================================
// Implement your decompressor here.
// ===========================================================================

/// The interface your decompressor must provide.
///
/// `input` is the raw bytes of a compressed file (for volume entries, the
/// FIRST volume of a split set — see below). Return the decompressed bytes,
/// or an error if the format/container is not yet supported.
///
/// For a `is_volume == true` entry, the test data is split across several
/// files on disk, but your decompressor is expected to reassemble them. The
/// harness passes only `path` (the first volume) plus a `volume_dir` hint so
/// you can locate the other parts, e.g. by globbing.
trait Decompressor {
    /// Decompress a single, non-volume file.
    fn decompress(&self, entry: &Entry, input: &[u8]) -> Result<Vec<u8>, Box<dyn Error>>;

    /// Decompress a split-volume set given the first volume's path.
    /// The default implementation falls back to `decompress` on the first
    /// volume, which works for formats that embed everything in part 1.
    fn decompress_volume(&self, entry: &Entry, input: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        self.decompress(entry, input)
    }
}

/// =========================================================================
/// TODO: replace this stub with your own implementation.
///
/// You receive `input` (compressed bytes) and must return the decompressed
/// bytes. Which format you are dealing with is in `entry.format`.
/// =========================================================================
struct MyDecompressor {
    cwd: std::path::PathBuf,
}

impl Decompressor for MyDecompressor {
    fn decompress(&self, entry: &Entry, _input: &[u8]) -> Result<Vec<u8>, Box<dyn Error>> {
        // Example: handle every format by shelling out to reference tools.
        // This is only a placeholder so the harness runs end-to-end; in your
        // real project, implement the actual decompression here.
        let path = &entry.path;
        let cwd = &self.cwd;
        match entry.format.as_str() {
            "gzip" => tool("gzip", &["-dc", path], cwd),
            "bzip2" => tool("bzip2", &["-dc", path], cwd),
            "xz" => tool("xz", &["-dc", path], cwd),
            "lzma" => tool("lzma", &["-dc", path], cwd),
            "lz4" => tool("lz4", &["-dc", path], cwd),
            "zstd" => tool("zstd", &["-dc", path], cwd),
            "brotli" => tool("brotli", &["-dc", path], cwd),
            "zip" => {
                if let Some(pw) = &entry.password {
                    tool("unzip", &["-P", pw, "-p", path], cwd)
                } else {
                    tool("unzip", &["-p", path], cwd)
                }
            }
            "7z" => {
                if let Some(pw) = &entry.password {
                    tool("7z", &["x", "-so", "-y", &format!("-p{pw}"), path], cwd)
                } else {
                    tool("7z", &["x", "-so", "-y", path], cwd)
                }
            }
            "rar" => {
                if let Some(pw) = &entry.password {
                    tool("unrar", &["p", "-inul", &format!("-p{pw}"), path], cwd)
                } else {
                    tool("unrar", &["p", "-inul", path], cwd)
                }
            }
            other => Err(format!("unsupported format: {other}").into()),
        }
    }
}

fn tool(name: &str, args: &[&str], cwd: &Path) -> Result<Vec<u8>, Box<dyn Error>> {
    let out = std::process::Command::new(name)
        .args(args)
        .current_dir(cwd)
        .output()?;
    if !out.status.success() {
        return Err(format!(
            "{name} exited with {}: {}",
            out.status,
            String::from_utf8_lossy(&out.stderr)
        )
        .into());
    }
    Ok(out.stdout)
}

// ===========================================================================
// End of user implementation.
// ===========================================================================

fn sha256(data: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(data);
    hex::encode(h.finalize())
}

fn run() -> Result<(), Box<dyn Error>> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf();
    let manifest_path = root.join("manifest.json");

    if !root.join("normal").is_dir() || !root.join("rawfiles").is_dir() {
        return Err(
            "Data not found. Compressed files are hosted in the GitHub Release — \
             download the tarballs and extract them into the repo root first. \
             See README.md".into(),
        );
    }
    let raw: Manifest = serde_json::from_str(&fs::read_to_string(&manifest_path)?)?;

    let d = MyDecompressor { cwd: root.clone() };
    let mut pass = 0usize;
    let mut fail = 0usize;
    let skip_big = std::env::var("SKIP_COMBINATION").is_ok();

    for entry in &raw.entries {
        if skip_big && entry.kind == "combination" {
            println!("[skip] {path} (SKIP_COMBINATION set)", path = entry.path);
            continue;
        }
        let full = root.join(&entry.path);
        if !full.exists() {
            println!("MISSING {path}", path = entry.path);
            fail += 1;
            continue;
        }
        let input = fs::read(&full)?;
        let result = if entry.is_volume {
            d.decompress_volume(entry, &input)
        } else {
            d.decompress(entry, &input)
        };

        match result {
            Ok(bytes) => {
                let got = sha256(&bytes);
                let ok = got == entry.expected_sha256;
                let mark = if ok { "ok" } else { "MISMATCH" };
                println!(
                    "[{mark}] {path} ({fmt}/{lvl}) len={} {got}",
                    bytes.len(),
                    path = entry.path,
                    fmt = entry.format,
                    lvl = entry.level,
                );
                if ok {
                    pass += 1;
                } else {
                    fail += 1;
                }
            }
            Err(e) => {
                println!("[error] {path}: {e}", path = entry.path);
                fail += 1;
            }
        }
    }

    println!("\nPASS: {pass}  FAIL: {fail}");
    if fail > 0 {
        return Err("some vectors failed".into());
    }
    println!("All positive test vectors verified OK.");

    // --- Negative cases: a correct decompressor must REJECT these ----------
    let faults_path = root.join("faults").join("manifest.json");
    if faults_path.exists() {
        let faults: FaultManifest =
            serde_json::from_str(&fs::read_to_string(&faults_path)?)?;
        let mut np = 0usize;
        let mut nf = 0usize;
        for fe in &faults.entries {
            let full = root.join(&fe.path);
            if !full.exists() {
                println!("MISSING {path}", path = fe.path);
                nf += 1;
                continue;
            }
            let input = fs::read(&full)?;
            // For negative cases, pass the (wrong) password through.
            let entry = Entry {
                layer: "fault".into(),
                kind: "fault".into(),
                path: fe.path.clone(),
                format: fe.format.clone(),
                level: "fault".into(),
                is_archive: false,
                is_volume: false,
                volume_count: None,
                password: fe.password.clone(),
                expected_file: String::new(),
                expected_size: 0,
                expected_sha256: String::new(),
            };
            match d.decompress(&entry, &input) {
                Ok(_) => {
                    println!("[neg-fail] {path}: decompressed but should have been rejected ({reason})",
                        path = fe.path, reason = fe.reason);
                    nf += 1;
                }
                Err(_) => {
                    println!("[neg-ok] {path} ({reason})", path = fe.path, reason = fe.reason);
                    np += 1;
                }
            }
        }
        println!("\nNEG-PASS: {np}  NEG-FAIL: {nf}");
        if nf > 0 {
            return Err("some negative cases were not rejected".into());
        }
        println!("All negative test vectors rejected OK.");
    }

    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("harness error: {e}");
        std::process::exit(1);
    }
}
