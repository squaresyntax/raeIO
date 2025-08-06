import streamlit.web.cli as stcli


def main() -> None:
    """Launch the Streamlit UI."""
    stcli.main(["run", "ui.py"])


if __name__ == "__main__":
    main()
