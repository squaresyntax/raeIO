from streamlit.web import cli as stcli


def main():
    """Launch the Streamlit UI programmatically."""
    stcli.main(["run", "ui.py"])


if __name__ == "__main__":
    main()
