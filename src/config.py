import os
# Get  the env
env = os.getenv("ENV", "local")

if env == "local":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/ktb-in-scrape")
elif env == "docker":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@database-ktb-in:5432/ktb-in-scrape")
#elif env == "prod":
#    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@proddb:5432/ktb-scrape")

else:
    DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise Exception("DATABASE_URL not found in environment!")