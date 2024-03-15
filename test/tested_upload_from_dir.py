from ivette.processing import upload_from_dir


dev = True
upload_from_dir("tmp", dev, ".out", instruction="Temps")
