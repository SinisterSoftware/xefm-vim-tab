"""テキストファイルを Windows Terminal の別タブの vim で開く (~/.xefm/extensions/vim_tab.py)

edit_file (E / F4) を置き換える。
  - テキストファイル (ローカル) 以外は、本来の edit_file に任せる。
  - タイトル XEFM-VIM のタブで vim (--servername XEFM) が動いていれば、その vim の新しいタブで開き、
    そのターミナルタブへ切り替える。
  - 動いていなければ、Windows Terminal に新しいタブを作って vim を起動する。

前提: vim が +clientserver 付き、wt (Windows Terminal) が PATH にある。
タブの切り替えは UI Automation (PowerShell) で行う。切り替えに失敗してもファイルは開く。
"""
import subprocess

SERVER = "XEFM"
TAB_TITLE = "XEFM-VIM"
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

_FOCUS_TAB = r"""
Add-Type -AssemblyName UIAutomationClient
$A = [System.Windows.Automation.AutomationElement]
$cond = New-Object System.Windows.Automation.AndCondition(
  (New-Object System.Windows.Automation.PropertyCondition($A::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)),
  (New-Object System.Windows.Automation.PropertyCondition($A::NameProperty, '%s')))
$tab = $A::RootElement.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if ($tab) { $tab.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select() }
""" % TAB_TITLE


def _is_text(path):
    if "://" in str(path):
        return False
    try:
        with open(str(path), "rb") as f:
            head = f.read(8192)
    except OSError:
        return False
    return b"\x00" not in head


def _vim_running():
    try:
        out = subprocess.run(["vim", "--serverlist"], capture_output=True, text=True,
                             timeout=10, creationflags=_NO_WINDOW).stdout
    except (OSError, subprocess.SubprocessError):
        return False
    return SERVER in out.upper().split()


def _focus_tab():
    subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", _FOCUS_TAB],
                     creationflags=_NO_WINDOW)


def open_in_vim(path):
    path = str(path)
    if _vim_running():
        subprocess.run(["vim", "--servername", SERVER, "--remote-tab-silent", path],
                       timeout=10, creationflags=_NO_WINDOW)
        _focus_tab()
    else:
        subprocess.Popen(["wt", "-w", "0", "new-tab", "--title", TAB_TITLE, "--suppressApplicationTitle",
                          "vim", "--servername", SERVER, path])


def edit_in_vim(ctx):
    """E / F4: カーソル下がテキストファイルなら vim のタブで開く。それ以外は標準の edit_file。"""
    e = ctx.pane.focused
    if e is not None and e.is_file and _is_text(e.path):
        try:
            open_in_vim(e.path)
            return
        except Exception as ex:
            ctx.message(f"vim 起動失敗: {ex}")
    ctx.invoke("edit_file")


ACTIONS = {"edit_file": {"func": edit_in_vim, "override": True}}
