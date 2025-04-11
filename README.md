
## IMPORTANT - READ BEFORE RUNNING
If all else fails, spam the ctrl + c buttons  
*or just kill the running terminals cuz it uses a lot of memory*


## Runnning the scripts
### APK Downloader
`python app_downloader_mobile-baidu.py`

### APK Analyser
Be sure to download docker container for mobsf using this command:  
`docker pull opensecurity/mobile-security-framework-mobsf:latest`

Start docker with:  
`docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest`

The run this command to start the script:  
`python mobsf_automated.py`


## Running mobsf locally (Docker Commands)
We can run the mobsf locally using the given user interface or using their REST apis.

`docker pull opensecurity/mobile-security-framework-mobsf:latest`  
`docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest`

Then go to localhost:8000 in your browser  
Then enter the default username and password and sign in

Default username: mobsf  
Default password: mobsf

