from contextlib import contextmanager
from pathlib import Path
import traceback
import pathlib
import os
import sys
import re
import platform
import subprocess
import logging
import arrow
from InquirerPy.utils import patched_print
import ofscraper.constants as constants
import ofscraper.utils.profiles as profiles
import ofscraper.utils.config as config_
import ofscraper.utils.args as args_
import ofscraper.utils.console as console_
from .profiles import get_current_profile


console=console_.shared_console
homeDir=pathlib.Path.home()
log=logging.getLogger(__package__)


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

        Args:``
            path (``Path): The path to the cwd

    Yields:
        None
    """


    origin = Path().absolute()
    createDir(Path(str(path)))
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
def createDir(path):
    try:
        path.mkdir(exist_ok=True,parents=True)
    except:
        log.info("Error creating directory, check the directory and make sure correct permissions have been issued.")
        sys.exit()
def databasePathHelper(model_id,username):
    configpath= get_config_path().parent
    profile=profiles.get_current_profile()
    model_username=username
    username=username
    modelusername=username
    modelusername=username
    model_id=model_id
    sitename="Onlyfans"
    site_name="Onlyfans"
    first_letter=username[0]
    save_location=config_.get_save_location(config_.read_config())
    if config_.get_allow_code_execution(config_.read_config()):
        formatStr=eval("f'{}'".format(config_.get_metadata(config_.read_config())))
    else:
        formatStr=config_.get_metadata(config_.read_config()).format(
                         profile=profile,
                         model_username=username,
                         username=username,
                         model_id=model_id,
                         sitename=site_name,
                         site_name=site_name,
                         first_letter=first_letter,
                         save_location=save_location,
                         configpath=configpath)


    formatStr
    return pathlib.Path(formatStr,"user_data.db")

def getmediadir(ele,username,model_id):
    sitename="onlyfans"
    site_name="onlyfans"
    post_id=ele.postid
    media_id=ele.id
    first_letter=username[0].capitalize()
    mediatype=ele.mediatype.capitalize()
    value=ele.value.capitalize()
    date=arrow.get(ele.postdate).format(config_.get_date(config_.read_config()))
    model_username=username
    responsetype=ele.responsetype
    root= pathlib.Path((config_.get_save_location(config_.read_config())))
    if config_.get_allow_code_execution(config_.read_config()):
        downloadDir=eval("f'{}'".format(config_.get_dirformat(config_.read_config())))
    else:
        downloadDir=config_.get_dirformat(config_.read_config())\
        .format(post_id=post_id,
                sitename=site_name,
                site_name=site_name,
                username=model_username,
                modeluesrname=model_username,
                first_letter=first_letter,
                model_id=model_id,
                model_username=username,
                responsetype=responsetype,
                mediatype=mediatype,
                date=date,
                value=value)
        
    return root /downloadDir  







def cleanup():
    log.info("Cleaning up .part files\n\n")
    root= pathlib.Path((config_.get_save_location(config_.read_config())))
    for file in list(filter(lambda x:re.search("\.part$",str(x))!=None,root.glob("**/*"))):
        file.unlink(missing_ok=True)


def getcachepath():
    profile = profiles.get_current_profile()
    path= get_config_path().parent/ profile/"cache"
    createDir(path.parent)
    return path
def trunicate(path):
    if args_.getargs().original:
        return path
    if platform.system() == 'Windows' and len(str(path))>256:
        return _windows_trunicateHelper(path)
    elif platform.system() == 'Linux':
        return _linux_trunicateHelper(path)
    else:
        return pathlib.Path(path)
def _windows_trunicateHelper(path):
    path=pathlib.Path(path)
    dir=path.parent
    file=path.name
    match=re.search("_[0-9]+\.[a-z]*$",path.name,re.IGNORECASE) or re.search("\.[a-z]*$",path.name,re.IGNORECASE)
    if match:
        ext=match.group(0)
    else:
        ext=""
    #-1 is for / between parentdirs and file
    fileLength=256-len(ext)-len(str(dir))-1
    newFile=f"{re.sub(ext,'',file)[fileLength]}{ext}"
    final=pathlib.Path(dir,newFile)
    log.debug(f"path: {final} path size: {len(str(final))}")
    return pathlib.Path(dir,newFile)

def _linux_trunicateHelper(path):
    path=pathlib.Path(path)
    dir=path.parent
    match=re.search("_[0-9]+\.[a-z]*$",path.name,re.IGNORECASE) or re.search("\.[a-z]*$",path.name,re.IGNORECASE)
    ext= match.group(0) if match else ""
    file=re.sub(ext,"",path.name)
    maxbytes=254-len(ext.encode('utf8'))
    small=0
    large=len(file)
    target=None
    maxLength=254-len(ext)
    if len(path.name.encode('utf8'))<=maxbytes:
        target=large
    while True and not target:
        if len(file[:large].encode('utf8'))==maxbytes:
            target=large
        elif len(file[:small].encode('utf8'))==maxbytes:
            target=small
        elif large==small:
            target=large
        elif large==small+1:
            target=small
        elif len(file[:large].encode('utf8'))>maxbytes:
            large=int((small+large)/2)
        elif len(file[:large].encode('utf8'))<maxbytes:
             small=large
             large=int((large+maxLength)/2)        
    newFile=f"{file[:target]}{ext}"
    log.debug(f"path: {path} filename bytesize: {len(newFile.encode('utf8'))}")
    return pathlib.Path(dir,newFile)



def mp4decryptchecker(x):
   return mp4decryptpathcheck(x) and mp4decryptexecutecheck(x)

def mp4decryptpathcheck(x):
    if not pathlib.Path(x).is_file():
        patched_print("path to mp4decrypt is not valid")
        return False
    return True
def mp4decryptexecutecheck(x):
    try:
        t=subprocess.run([x],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if re.search("mp4decrypt",t.stdout.decode())!=None or  re.search("mp4decrypt",t.stderr.decode())!=None:
            return True
        patched_print("issue executing path as mp4decrypt")
    except Exception as E:
        patched_print(E)
        patched_print(traceback.format_exc())
        return False


def ffmpegchecker(x):
    return ffmpegexecutecheck(x) and ffmpegpathcheck(x)

def ffmpegpathcheck(x):
    if not pathlib.Path(x).is_file():
        patched_print("path to ffmpeg is not valid")
        return False
    return True 

def ffmpegexecutecheck(x):
    try:
        t=subprocess.run([x],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if re.search("ffmpeg",t.stdout.decode())!=None or  re.search("ffmpeg",t.stderr.decode())!=None:
            return True
        patched_print("issue executing path as ffmpeg")
    except Exception as E:
        patched_print(E)
        patched_print(traceback.format_exc())
        return False  
   
def getlogpath():
    path= get_config_path().parent / "logging"/f'ofscraper_{config_.get_main_profile()}_{arrow.now().format("YYYY-MM-DD")}.log'
    createDir(path.parent)
    return path

def get_config_path():
    t=pathlib.Path(args_.getargs().config or pathlib.Path.home() / constants.configPath)        
    if t.is_file():
         return t
    elif t.parent.is_dir():
        t/constants.configFile
    return t/constants.configFile

def get_auth_file():
    profile = get_current_profile()
    auth= get_config_path().parent/profile /constants.authFile if not args_.getargs().auth else args_.getargs().auth
    if auth.is_dir():
        raise Exception("Auth File must be a file")
    return auth

    
   
