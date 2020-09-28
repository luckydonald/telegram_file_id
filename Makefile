MY_VAR := ${shell python -c 'from tg_file_id import VERSION as v; print(v)'}

clean:
	rm -rf *.so *.egg-info build *.png *.log *.svg

upload: clean
	python setup.py sdist
	@echo UPLOADING VERSION $(MY_VAR)
	twine upload dist/tg_file_id-${MY_VAR}.tar.gz
