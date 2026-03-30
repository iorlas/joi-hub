import hashlib
from urllib.parse import quote

import bencodepy


def is_private_torrent(data: bytes) -> bool:
    """Check if .torrent file is from a private tracker.

    Private torrents set info.private=1 and must NOT be converted to magnet
    links — the tracker validates against registered .torrent downloads and
    rejects magnet-derived peers ("user not found").
    """
    try:
        torrent: dict = bencodepy.decode(data)  # type: ignore[assignment]
        info = torrent[b"info"]
    except (bencodepy.DecodingError, KeyError):
        return False
    return info.get(b"private", 0) == 1


def torrent_bytes_to_magnet(data: bytes) -> str:
    """Convert .torrent file bytes to a magnet link.

    Raises ValueError if the torrent is private — private torrents must be
    added as .torrent files, not magnet links.
    """
    try:
        torrent: dict = bencodepy.decode(data)  # type: ignore[assignment]
        info = torrent[b"info"]
    except (bencodepy.DecodingError, KeyError) as e:
        msg = "Invalid .torrent file data"
        raise ValueError(msg) from e

    if info.get(b"private", 0) == 1:
        msg = "Cannot convert private tracker .torrent to magnet — use the .torrent file directly"
        raise ValueError(msg)

    info_encoded = bencodepy.encode(info)
    info_hash = hashlib.sha1(info_encoded).hexdigest()  # noqa: S324

    magnet = f"magnet:?xt=urn:btih:{info_hash}"

    name = info.get(b"name")
    if name:
        magnet += f"&dn={quote(name.decode(errors='replace'))}"

    if b"announce" in torrent:
        magnet += f"&tr={quote(torrent[b'announce'].decode(errors='replace'))}"

    return magnet
