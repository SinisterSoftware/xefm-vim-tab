from vim_tab.logic import _is_text

def test_is_text_checks_local_file_contents(tmp_path):
    text = tmp_path / "text.txt"
    binary = tmp_path / "binary.bin"
    text.write_bytes(b"plain text\n")
    binary.write_bytes(b"a\x00b")
    assert _is_text(text)
    assert not _is_text(binary)
