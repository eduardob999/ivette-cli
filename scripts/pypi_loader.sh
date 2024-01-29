source .env
python3 setup.py sdist bdist_wheel
twine upload dist/* <<< "__token__
"
rm -r dist
rm -r build
rm -r ivette_client.egg-info