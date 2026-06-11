from amiii.tools.browser import BrowserTool

if __name__ == "__main__":
    tool = BrowserTool()

    result = tool.play_youtube_video(
        "Believer Imagine Dragons"
    )

    print(result)