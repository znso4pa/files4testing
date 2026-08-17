//! CSO (PSP CISO) compressed ISO: writer + reader for self-check.
//!
//! Layout:
//!   header: magic "CISO" + u32 header_size + u64 total_bytes + u32 block_size
//!   index:  (nblocks + 1) u32 entries; bit31 = zlib flag, low 31 bits =
//!           ABSOLUTE file offset of the block, >> 1.
//!   data:   zlib or raw blocks; every block start is 2-byte aligned.

pub const CSO_BLOCK_SIZE: u32 = 2048;

pub fn iso_to_cso(iso: &[u8], block_size: u32) -> Vec<u8> {
    let bs = block_size as usize;
    let nblocks = iso.len().div_ceil(bs);
    let header_size: usize = 0x18;
    let mut data_start = header_size + (nblocks + 1) * 4;
    if data_start % 2 != 0 {
        data_start += 1; // keep offset>>1 encoding lossless
    }

    let mut idx: Vec<u32> = Vec::with_capacity(nblocks + 1);
    let mut data: Vec<u8> = Vec::new();
    for i in 0..nblocks {
        let start = i * bs;
        let end = (start + bs).min(iso.len());
        let block = &iso[start..end];
        let abs_off = data_start + data.len();
        // zlib (RFC1950) attempt
        let mut comp = flate2::Compress::new(flate2::Compression::default(), true);
        let mut cbuf = vec![0u8; block.len() + 128];
        let compressed = comp.compress(block, &mut cbuf, flate2::FlushCompress::Finish).is_ok()
            && (comp.total_out() as usize) > 0
            && (comp.total_out() as usize) < block.len();
        if compressed {
            cbuf.truncate(comp.total_out() as usize);
            idx.push(0x8000_0000 | ((abs_off as u32) >> 1));
            data.extend_from_slice(&cbuf);
        } else {
            idx.push((abs_off as u32) >> 1); // raw block, high bit 0
            data.extend_from_slice(block);
        }
        // align each block start to an even offset
        if data.len() % 2 == 1 {
            data.push(0);
        }
    }
    idx.push(((data_start + data.len()) as u32) >> 1); // sentinel = end of data

    let mut out = Vec::with_capacity(data_start + data.len());
    out.extend_from_slice(b"CISO");
    out.extend_from_slice(&(header_size as u32).to_le_bytes());
    out.extend_from_slice(&(iso.len() as u64).to_le_bytes());
    out.extend_from_slice(&block_size.to_le_bytes());
    while out.len() < header_size {
        out.push(0);
    }
    for x in &idx {
        out.extend_from_slice(&x.to_le_bytes());
    }
    while out.len() < data_start {
        out.push(0);
    }
    out.extend_from_slice(&data);
    out
}

pub fn cso_to_iso(cso: &[u8]) -> Result<Vec<u8>, String> {
    if cso.len() < 0x18 || &cso[0..4] != b"CISO" {
        return Err("bad cso magic".into());
    }
    let _header_size = u32::from_le_bytes(cso[4..8].try_into().unwrap()) as usize;
    let total = u64::from_le_bytes(cso[8..16].try_into().unwrap()) as usize;
    let block_size = u32::from_le_bytes(cso[16..20].try_into().unwrap()) as usize;
    let bs = block_size.max(1);
    let nblocks = total.div_ceil(bs);
    let read_idx = |i: usize| -> u32 {
        let off = 0x18 + i * 4;
        u32::from_le_bytes(cso[off..off + 4].try_into().unwrap())
    };
    if nblocks + 1 > cso.len().saturating_sub(0x18) / 4 {
        return Err("cso index out of bounds".into());
    }
    let mut out = Vec::with_capacity(total);
    for i in 0..nblocks {
        let e = read_idx(i);
        let compressed = (e & 0x8000_0000) != 0;
        let start = ((e & 0x7fff_ffff) as usize) << 1;
        let end = ((read_idx(i + 1) & 0x7fff_ffff) as usize) << 1;
        let block_len = bs.min(total - i * bs);
        if start > cso.len() || end > cso.len() || end < start {
            return Err("cso block out of bounds".into());
        }
        if compressed {
            let mut d = flate2::Decompress::new(true);
            let mut buf = vec![0u8; bs];
            d.decompress(&cso[start..end], &mut buf, flate2::FlushDecompress::Finish)
                .map_err(|e| e.to_string())?;
            out.extend_from_slice(&buf[..d.total_out() as usize]);
        } else {
            out.extend_from_slice(&cso[start..start + block_len]);
        }
    }
    out.truncate(total);
    Ok(out)
}