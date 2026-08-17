//! Minimal POSIX ustar tar writer for multi-file / symlink test vectors.

pub enum TarKind {
    File,
    Dir,
    Symlink,
}

pub struct TarEntry {
    pub path: String,
    pub kind: TarKind,
    pub data: Vec<u8>,
    pub link: String,
}

fn write_field(h: &mut [u8; 512], start: usize, len: usize, content: &[u8]) {
    let n = content.len().min(len);
    h[start..start + n].copy_from_slice(&content[..n]);
}

pub fn build_tar(entries: &[TarEntry]) -> Vec<u8> {
    let mut out = Vec::new();
    for e in entries {
        let mut h = [0u8; 512];
        let name = e.path.as_bytes();
        write_field(&mut h, 0, 100, name);
        match e.kind {
            TarKind::File => {
                write_field(&mut h, 100, 8, b"0000644\0");
                write_field(&mut h, 156, 1, b"0");
                let size = format!("{:011o}\0", e.data.len());
                write_field(&mut h, 124, 12, size.as_bytes());
            }
            TarKind::Dir => {
                write_field(&mut h, 100, 8, b"0000755\0");
                write_field(&mut h, 156, 1, b"5");
                write_field(&mut h, 124, 12, b"00000000000\0");
            }
            TarKind::Symlink => {
                write_field(&mut h, 100, 8, b"0000777\0");
                write_field(&mut h, 156, 1, b"2");
                write_field(&mut h, 124, 12, b"00000000000\0");
                write_field(&mut h, 157, 100, e.link.as_bytes());
            }
        }
        write_field(&mut h, 108, 8, b"0000000\0");
        write_field(&mut h, 116, 8, b"0000000\0");
        write_field(&mut h, 136, 12, b"00000000000\0");
        write_field(&mut h, 148, 8, b"        ");
        write_field(&mut h, 257, 6, b"ustar\0");
        write_field(&mut h, 263, 2, b"00");
        write_field(&mut h, 265, 32, b"root\0");
        write_field(&mut h, 297, 32, b"root\0");
        // checksum: sum over the header with the checksum field as spaces
        let sum: u32 = h.iter().map(|b| *b as u32).sum();
        let chk = format!("{:06o}\0 ", sum);
        write_field(&mut h, 148, 8, chk.as_bytes());
        out.extend_from_slice(&h);
        if !e.data.is_empty() {
            out.extend_from_slice(&e.data);
            while out.len() % 512 != 0 {
                out.push(0);
            }
        }
    }
    out.extend_from_slice(&[0u8; 1024]);
    out
}