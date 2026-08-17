//! gen_corpus — generates the v1.2 test vectors that need hand-written
//! writers or byte derivation: CSO (from the ISO files produced by
//! gen_v12.sh), multi-file tar (+ compressed variants), multi-member gzip /
//! zstd streams, and the machine-readable corpus_spec.json consumed by
//! gen_manifest.py.
//!
//! Run after `gen_v12.sh` (which creates the ISO files) and after
//! `compress.sh` (which creates the base gzip/zstd vectors).

mod cso;
mod tarx;

use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn sha256(data: &[u8]) -> String {
    let mut h = Sha256::new();
    h.update(data);
    hex(&h.finalize())
}

fn hex(d: &[u8]) -> String {
    d.iter().map(|b| format!("{b:02x}")).collect()
}

fn run(cwd: &Path, cmd: &str, args: &[&str]) -> Result<(), String> {
    let st = Command::new(cmd)
        .args(args)
        .current_dir(cwd)
        .output()
        .map_err(|e| format!("{cmd}: {e}"))?;
    if !st.status.success() {
        let msg = String::from_utf8_lossy(&st.stderr);
        return Err(format!("{cmd} failed: {msg}"));
    }
    Ok(())
}

fn spec_json(entries: &[serde_json::Value]) -> serde_json::Value {
    serde_json::json!({ "version": 1, "entries": entries })
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .unwrap()
        .to_path_buf();
    let mut spec: Vec<serde_json::Value> = Vec::new();

    // ---- CSO from single-file ISOs --------------------------------------
    for kind in ["rawfile1", "rawfile2", "rawfile5", "rawfile6"] {
        let iso_path = root.join(format!("normal/{kind}/{kind}.iso"));
        let cso_path = root.join(format!("normal/{kind}/{kind}.iso.cso"));
        if !iso_path.exists() {
            eprintln!("skip {kind}: {} not found (run gen_v12.sh first)", iso_path.display());
            continue;
        }
        let iso = fs::read(&iso_path)?;
        let cso = cso::iso_to_cso(&iso, cso::CSO_BLOCK_SIZE);
        // self-check round trip
        let back = cso::cso_to_iso(&cso).map_err(|e| format!("{kind} cso self-check: {e}"))?;
        assert_eq!(back, iso, "{kind} cso round trip mismatch");
        fs::write(&cso_path, &cso)?;
        let rel_iso = format!("normal/{kind}/{kind}.iso");
        let rel_cso = format!("normal/{kind}/{kind}.iso.cso");
        spec.push(serde_json::json!({
            "path": rel_cso,
            "layer": "normal",
            "kind": kind,
            "format": "cso",
            "level": "iso",
            "is_archive": true,
            "expected_file": rel_iso,
            "expected_size": iso.len(),
            "expected_sha256": sha256(&iso),
            "note": "CSO of a single-file ISO; decompress -> ISO byte stream",
        }));
        println!("cso {kind}: {} -> {} bytes", rel_iso, cso.len());
    }

    // ---- multi-file tar tree (+ symlink) + compressed variants ----------
    let tree_files: Vec<(&str, &str)> = vec![
        ("rawfile1.txt", "rawfiles/rawfile1.txt"),
        ("data/rawfile2.jpg", "rawfiles/rawfile2.jpg"),
        ("data/rawfile6.json", "rawfiles/rawfile6.json"),
        ("data/sub/rawfile7.c", "rawfiles/rawfile7.c"),
    ];
    let mut tar_entries: Vec<tarx::TarEntry> = Vec::new();
    tar_entries.push(tarx::TarEntry {
        path: "data".to_string(),
        kind: tarx::TarKind::Dir,
        data: Vec::new(),
        link: String::new(),
    });
    tar_entries.push(tarx::TarEntry {
        path: "data/sub".to_string(),
        kind: tarx::TarKind::Dir,
        data: Vec::new(),
        link: String::new(),
    });
    for (path, raw) in &tree_files {
        let data = fs::read(root.join(raw))?;
        tar_entries.push(tarx::TarEntry {
            path: path.to_string(),
            kind: tarx::TarKind::File,
            data,
            link: String::new(),
        });
    }
    tar_entries.push(tarx::TarEntry {
        path: "link_to_rawfile1.txt".to_string(),
        kind: tarx::TarKind::Symlink,
        data: Vec::new(),
        link: "rawfile1.txt".to_string(),
    });
    let tar = tarx::build_tar(&tar_entries);
    let tar_dir = root.join("normal/rawfile_tree");
    fs::create_dir_all(&tar_dir)?;
    fs::write(tar_dir.join("rawfile_tree.tar"), &tar)?;

    let files_spec: Vec<serde_json::Value> = tree_files
        .iter()
        .map(|(path, raw)| serde_json::json!({ "path": path, "raw": raw }))
        .collect();

    let tree_spec_entry = |fmt: &str, level: &str, path: &str, note: &str| -> serde_json::Value {
        serde_json::json!({
            "path": path,
            "layer": "normal",
            "kind": "rawfile_tree",
            "format": fmt,
            "level": level,
            "files": files_spec,
            "note": note,
        })
    };
    spec.push(tree_spec_entry("iso", "tree",
        "normal/rawfile_tree/rawfile_tree.iso",
        "ISO9660 with a directory tree (multi-file)."));
    spec.push(tree_spec_entry("tar", "tree",
        "normal/rawfile_tree/rawfile_tree.tar",
        "Multi-file tar with a directory tree plus one symlink member."));

    // compressed tar variants (shell out to reference CLIs)
    let variants: Vec<(&str, &str, &[&str])> = vec![
        ("rawfile_tree.tar.g9.tar.gz", "gzip", &["-9", "-c", "rawfile_tree.tar"]),
        ("rawfile_tree.tar.b9.tar.bz2", "bzip2", &["-9", "-c", "rawfile_tree.tar"]),
        ("rawfile_tree.tar.x9.tar.xz", "xz", &["-9", "-c", "rawfile_tree.tar"]),
        ("rawfile_tree.tar.zst-19.tar.zst", "zstd", &["-19", "-c", "rawfile_tree.tar"]),
    ];
    for (out_name, tool, args) in &variants {
        let out = fs::File::create(tar_dir.join(out_name))?;
        let mut child = Command::new(tool)
            .args(*args)
            .current_dir(&tar_dir)
            .stdout(std::process::Stdio::from(out))
            .stderr(std::process::Stdio::null())
            .spawn()
            .map_err(|e| format!("{tool} spawn: {e}"))?;
        let st = child.wait()?;
        if !st.success() {
            return Err(format!("{tool} failed for {out_name}").into());
        }
        let inner_fmt = out_name
            .split('.')
            .last()
            .map(|e| match e {
                "gz" => "tar.gzip",
                "bz2" => "tar.bzip2",
                "xz" => "tar.xz",
                "zst" => "tar.zstd",
                _ => "tar.??",
            })
            .unwrap_or("tar.??");
        let level = out_name.rsplit('.').nth(2).unwrap_or("tree");
        spec.push(tree_spec_entry(
            inner_fmt, level, &format!("normal/rawfile_tree/{out_name}"),
            "Compressed multi-file tar tree."));
    }
    println!("tar tree: {} bytes ({} variants)", tar.len(), variants.len());

    // ---- multi-member gzip / zstd streams -------------------------------
    let gz1 = fs::read(root.join("normal/rawfile1/rawfile1.g9.gz"))?;
    let gz_multi = [gz1.as_slice(), gz1.as_slice()].concat();
    fs::write(root.join("normal/rawfile1/rawfile1.g9.multi.gz"), &gz_multi)?;
    let raw1 = fs::read(root.join("rawfiles/rawfile1.txt"))?;
    let mut exp = raw1.clone();
    exp.extend_from_slice(&raw1);
    spec.push(serde_json::json!({
        "path": "normal/rawfile1/rawfile1.g9.multi.gz",
        "layer": "normal",
        "kind": "rawfile1",
        "format": "gzip",
        "level": "multi",
        "expected_file": null,
        "expected_size": exp.len(),
        "expected_sha256": sha256(&exp),
        "note": "Two concatenated gzip members of rawfile1.",
    }));

    let z1 = fs::read(root.join("normal/rawfile1/rawfile1.zst-19.zst"))?;
    let z_multi = [z1.as_slice(), z1.as_slice()].concat();
    fs::write(root.join("normal/rawfile1/rawfile1.zst-multi.zst"), &z_multi)?;
    spec.push(serde_json::json!({
        "path": "normal/rawfile1/rawfile1.zst-multi.zst",
        "layer": "normal",
        "kind": "rawfile1",
        "format": "zstd",
        "level": "multi",
        "expected_file": null,
        "expected_size": exp.len(),
        "expected_sha256": sha256(&exp),
        "note": "Two concatenated zstd frames of rawfile1.",
    }));

    // ---- write corpus_spec.json -----------------------------------------
    let spec_path = root.join("corpus_spec.json");
    fs::write(&spec_path, serde_json::to_string_pretty(&spec_json(&spec))?)?;
    println!("corpus_spec.json written: {} entries", spec.len());

    Ok(())
}