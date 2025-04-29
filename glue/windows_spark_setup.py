"""
python -m devops.windows_spark_setup
poetry run python -m glue.windows_spark_setup
"""

import os
import requests
import subprocess
import winreg
import shutil
import zipfile
import tarfile

BASE_DIR = r"D:\spark_setup\spark_3_3_2"
JAVA_DIR = os.path.join(BASE_DIR, "java")
SPARK_DIR = os.path.join(BASE_DIR, "spark")
HADOOP_DIR = os.path.join(BASE_DIR, "hadoop")
HADOOP_BIN_DIR = os.path.join(HADOOP_DIR, "bin")
os.makedirs(HADOOP_BIN_DIR, exist_ok=True)

CORRETTO_ZIP_URL = "https://corretto.aws/downloads/latest/amazon-corretto-17-x64-windows-jdk.zip"
SPARK_TGZ_URL = "https://archive.apache.org/dist/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz"
WINUTILS_RAW_URL = "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.0.2/bin/winutils.exe"

def download_file(url, destination_path):
    print(f"⬇️ Downloading {url}")
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            with open(destination_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        print(f"\r📦 Downloaded: {downloaded/1024/1024:.2f} MB / {total/1024/1024:.2f} MB", end="")
        print(f"\n✅ Saved to {destination_path}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        raise

def download_and_extract_zip(url, extract_to):
    local_zip = os.path.join(BASE_DIR, os.path.basename(url))
    download_file(url, local_zip)
    print(f"📦 Extracting Java ZIP to {extract_to}")
    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    os.remove(local_zip)

def download_and_extract_tgz(url, extract_to):
    local_tgz = os.path.join(BASE_DIR, os.path.basename(url))
    download_file(url, local_tgz)
    print(f"📦 Extracting Spark to {extract_to}")
    with tarfile.open(local_tgz, "r:gz") as tar:
        tar.extractall(path=extract_to)
    os.remove(local_tgz)

def set_system_env(var_name, value):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, var_name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        print(f"✅ Set {var_name} = {value}")
    except PermissionError:
        print(f"❌ Permission denied: Unable to set {var_name}. Run the script as Administrator.")

def add_to_system_path(path_to_add):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                             0, winreg.KEY_ALL_ACCESS)
        value, _ = winreg.QueryValueEx(key, 'Path')
        if path_to_add not in value:
            new_value = value + ";" + path_to_add
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_value)
            print(f"✅ Added to PATH: {path_to_add}")
        winreg.CloseKey(key)
    except PermissionError:
        print(f"❌ Permission denied: Unable to add {path_to_add} to PATH. Run the script as Administrator.")

def find_java_home_from_folder(folder):
    for item in os.listdir(folder):
        full = os.path.join(folder, item)
        if os.path.isdir(full) and "jdk" in item.lower():
            return full
    return None

def verify_setup(java_home, hadoop_home, spark_home):
    winutils_path = os.path.join(hadoop_home, "bin", "winutils.exe")
    print("\n🔍 Verifying Setup...\n")

    print("🧪 Checking Java...")
    try:
        result = subprocess.check_output(["java", "-version"], stderr=subprocess.STDOUT, text=True)
        print(result)
    except Exception as e:
        print("❌ Java test failed:", e)

    print("\n🧪 Checking winutils...")
    try:
        output = subprocess.check_output(
            [winutils_path, "ls", "/"],
            stderr=subprocess.STDOUT,
            text=True
        )
        print("✅ winutils works ✔")
    except Exception as e:
        print("❌ winutils.exe failed:", e)

    print("\n🧪 Checking SparkSession startup...")
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder \
            .appName("VerifySpark") \
            .master("local[2]") \
            .getOrCreate()
        spark.range(5).show()
        spark.stop()
        print("✅ SparkSession works ✔")
    except Exception as e:
        print("❌ SparkSession failed:", e)

def setup_environment():
    print("\n🚀 Starting Spark + Java + Hadoop Setup on Windows")

    # Step 1: Download and install Java (ZIP)
    download_and_extract_zip(CORRETTO_ZIP_URL, JAVA_DIR)
    java_home = find_java_home_from_folder(JAVA_DIR)
    if java_home:
        set_system_env("JAVA_HOME", java_home)
        add_to_system_path(os.path.join(java_home, "bin"))
    else:
        print("❌ Could not detect Java home after extracting ZIP.")

    # Step 2: Install Spark
    download_and_extract_tgz(SPARK_TGZ_URL, SPARK_DIR)
    spark_home = os.path.join(SPARK_DIR, "spark-3.3.1-bin-hadoop3")
    set_system_env("SPARK_HOME", spark_home)
    add_to_system_path(os.path.join(spark_home, "bin"))

    # Step 3: Download winutils.exe
    winutils_path = os.path.join(HADOOP_BIN_DIR, "winutils.exe")
    download_file(WINUTILS_RAW_URL, winutils_path)
    set_system_env("HADOOP_HOME", HADOOP_DIR)
    add_to_system_path(HADOOP_BIN_DIR)

    # Step 4: Verify
    verify_setup(java_home, HADOOP_DIR, spark_home)

    print("\n✅ Setup completed successfully.")
    print("🔄 Please restart your system or re-login to apply all environment changes.")

if __name__ == "__main__":
    setup_environment()