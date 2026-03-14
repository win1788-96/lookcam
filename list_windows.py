import pygetwindow as gw

def list_windows():
    print("目前的視窗標題列表：")
    for title in gw.getAllTitles():
        if title.strip():
            print(f"- {title}")

if __name__ == "__main__":
    list_windows()
