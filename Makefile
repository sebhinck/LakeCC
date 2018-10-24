all:
	python setup.py build_ext --inplace
#	cp ../LakeModel_test.py .
#	ln -sf ../InputData .
	
clean:
	python setup.py clean --all
	rm -f LakeCC.so cython/LakeCC.cpp 
