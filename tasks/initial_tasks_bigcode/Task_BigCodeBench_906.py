import os
import re
import zipfile
import shutil

def task_func(source_dir, target_dir, archive_name='archive.zip'):
    # Create directories if they don't exist
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(target_dir, exist_ok=True)
    
    archive_path = os.path.join(target_dir, archive_name)
    
    with zipfile.ZipFile(archive_path, 'w') as archive:
        for file in os.listdir(source_dir):
            if re.search(r'_processed$', os.path.splitext(file)[0]):
                archive.write(os.path.join(source_dir, file), arcname=file)
                shutil.move(os.path.join(source_dir, file), target_dir)
                
    return archive_path