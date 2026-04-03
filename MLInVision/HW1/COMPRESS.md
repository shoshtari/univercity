# PDF compression 

## GhostScript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
-dPDFSETTINGS=/ebook \
-dNOPAUSE -dQUIET -dBATCH \
-sOutputFile=compressed.pdf main.pdf 

## Use jpg instead of png


# Notebooks 
## Remove outputs
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace *.ipynb
