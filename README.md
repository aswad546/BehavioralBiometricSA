Install dependencies for graph construction and static analysis logic:
```
npm install
pip3 install -r requirements.txt
```
To run this you can use the following command:
```
python3 static.py --export filename
```
This should save the file to the /tmp directory

Run the following to enable the redis queue for batched writes:
`python queue_worker.py
`
Additionally modify the `.env` file
```
# Write mode: "immediate" or "batch"
DB_WRITE_MODE=immediate
```



