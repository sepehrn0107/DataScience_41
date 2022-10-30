# clean mypy cache
rm -rf .mypy_cache

# clean python cache
find src -type f -name '*.py[co]' -delete
find src -type d -name '__pycache__' -delete 
find . -type f -name '.DS_Store' -delete 