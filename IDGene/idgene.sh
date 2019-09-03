
#!/bin/bash

if [ -z "${PTH}" ]; then
  export PTH="$(dirname $0)/"
fi

echo "Posting random tweets with IDGene.py"

python3 ./app/IDGene.py