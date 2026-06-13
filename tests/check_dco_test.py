from __future__ import annotations

from pre_commit_hooks.check_dco import main


# ── success cases ──

def test_standard_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text(
        'feat: add search\n\n'
        'Signed-off-by: Alice <alice@example.com>\n',
    )
    assert main([str(msg)]) == 0


def test_multiple_signoffs(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text(
        'feat: co-authored\n\n'
        'Signed-off-by: Alice <alice@example.com>\n'
        'Signed-off-by: Bob <bob@example.com>\n',
    )
    assert main([str(msg)]) == 0


def test_signoff_in_body_middle(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text(
        'feat: stuff\n\nSome description.\n\n'
        'Signed-off-by: Alice <alice@example.com>\n\nMore text.\n',
    )
    assert main([str(msg)]) == 0


def test_full_name_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text(
        'fix: bug\n\n'
        'Signed-off-by: Alice Wonderland'
        ' <alice@wonderland.com>\n',
    )
    assert main([str(msg)]) == 0


def test_plus_address_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: x\n\nSigned-off-by: Alice <alice+dev@example.com>\n')
    assert main([str(msg)]) == 0


def test_multiline_body_with_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text(
        'feat: big change\n\n'
        'Paragraph one.\n\n'
        'Paragraph two.\n\n'
        'Signed-off-by: Alice <alice@example.com>\n',
    )
    assert main([str(msg)]) == 0


def test_no_argv_exits_1():
    assert main([]) == 1


# ── failure cases ──

def test_missing_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: quick fix\n')
    assert main([str(msg)]) == 1


def test_empty_message(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('')
    assert main([str(msg)]) == 1


def test_signoff_without_email(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: x\n\nSigned-off-by: JustName\n')
    assert main([str(msg)]) == 1


def test_signoff_without_name(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: x\n\nSigned-off-by: <anon@example.com>\n')
    assert main([str(msg)]) == 1


def test_lowercase_signoff_only(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: x\n\nsigned-off-by: alice <alice@example.com>\n')
    assert main([str(msg)]) == 1


def test_signoff_only_no_colon(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: x\n\nSigned-off-by alice <alice@example.com>\n')
    assert main([str(msg)]) == 1


# ── CLI / main() integration ──

def test_main_passes_with_valid_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: ok\n\nSigned-off-by: CI <ci@test.com>\n')
    assert main([str(msg)]) == 0


def test_main_fails_without_signoff(tmp_path):
    msg = tmp_path / 'msg'
    msg.write_text('feat: oops\n')
    assert main([str(msg)]) == 1
