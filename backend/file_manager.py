def download_file(bucket, file_name, local_path):
    try:
        response = supabase.storage.from_(bucket).download(file_name)
        with open(local_path, "wb") as f:
            f.write(response)
        return local_path
    except Exception as e:
        return f"Error al descargar {file_name}: {e}"
