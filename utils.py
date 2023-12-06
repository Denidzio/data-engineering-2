from requests import Response, get
from os import makedirs, path, remove
from zipfile import ZipFile


def get_filename_from_request(resp: Response) -> str:
    content_disposition = resp.headers.get("Content-Disposition")

    if content_disposition:
        return content_disposition.split("filename=")[-1].strip('"')
    else:
        return resp.url.split("/")[-1]


def unzip_contents(zip_save_dir: str, output_dir: str) -> None:
    with ZipFile(zip_save_dir, "r") as zip_ref:
        csv_files = [
            file
            for file in zip_ref.namelist()
            if file.endswith(".csv") and "__MACOSX" not in file
        ]

        if not csv_files:
            print("Не знайдено жодного CSV файлу в ZIP архіві.")
            return

        for csv_file in csv_files:
            zip_ref.extract(csv_file, path=output_dir)
            print(f"Файл {csv_file} успішно розпаковано.")

    remove(zip_save_dir)


def download_resource(url: str, output_dir: str) -> None:
    makedirs(output_dir, exist_ok=True)

    print(f"Завантаження ресурсів {url}...")

    response = get(url, allow_redirects=True)

    if response.status_code != 200:
        print(
            f"Сталася помилка під час отримання ресурсів з {url}. Код: {response.status_code}."
        )
        return

    content_type = response.headers.get("Content-Type")

    if "zip" not in content_type:
        print(f"Завантажений ресурс з {url} не є ZIP архівом.")
        return

    filename = get_filename_from_request(response)

    zip_save_dir = path.join(output_dir, filename)

    with open(zip_save_dir, "wb") as f:
        f.write(response.content)

    print(f"{filename} успішно збережно в папку {output_dir}.")

    unzip_contents(zip_save_dir, output_dir)
