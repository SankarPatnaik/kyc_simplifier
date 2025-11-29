from pathlib import Path
from simplifier import EmailSimplifier

def bulk_convert(input_dir: str, output_dir: str, config_path: str = "config.yaml"):
    simplifier = EmailSimplifier(config_path)
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    for file in in_path.rglob("*"):
        if file.is_file() and file.suffix.lower() in {".txt", ".md", ".html"}:
            content = file.read_text(encoding="utf-8")
            simplified = simplifier.simplify_text(content)
            target = out_path / file.relative_to(in_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(simplified, encoding="utf-8")
            print(f"Converted {file} -> {target}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    bulk_convert(args.input, args.output, args.config)
