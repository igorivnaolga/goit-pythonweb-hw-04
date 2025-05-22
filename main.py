import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="copy.log",
)

# Parse arguments from command line
parser = argparse.ArgumentParser(description="Sorting folder")
parser.add_argument("--source", "-s", required=True, help="Source folder")
parser.add_argument("--output", "-o", default="dest", help="Output folder")
args = parser.parse_args()
source_folder = AsyncPath(args.source)
output_folder = AsyncPath(args.output)  # dest


# Async recursion function to read folder
async def read_folder(path: AsyncPath) -> None:
    try:
        async for el in path.iterdir():
            if await el.is_dir():
                await read_folder(el)
            else:
                await copy_file(el)
    except Exception as e:
        logging.error(f"Error while reading folder {path}: {e} ")


# Async function to copy file
async def copy_file(file: AsyncPath) -> None:
    try:
        ext = file.suffix or "no_extension"
        dest_dir = output_folder / ext
        await dest_dir.mkdir(exist_ok=True, parents=True)

        dest_file = dest_dir / file.name
        if await dest_file.exists():
            logging.warning(f"File already exists and was skipped: {dest_file}")
            return

        await copyfile(file, dest_file)
        logging.info(f"Copied: {file} -> {dest_file}")
    except Exception as e:
        logging.error(f"Error while copy {file}: {e}")


# Main block to run
if __name__ == "__main__":
    try:
        asyncio.run(read_folder(source_folder))
        logging.info("Sorting complete")
    except Exception as e:
        logging.error(f"Error: {e}")
