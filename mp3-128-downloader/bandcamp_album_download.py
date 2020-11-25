#!/usr/bin/env python3
import json, os, requests, re
from bs4 import BeautifulSoup

path_query = re.compile( '[\/\*\$\;\<\>]' )
track_href = re.compile( '^\s*\<a\shref=\"(\/(track)[^\"]+)\"' )
album_href = re.compile( '^\s*\<a\shref=\"(\/(track|album)[^\"]+)\"' )
url_separator = re.compile( '\/\/([^\.]+)\.' )
track_searcher = re.compile( '\/(track)\/' )

def download( url ):
    TralbumData = ""
    scripts = []
    m=url_separator.search( url )
    group = m.group(1)
    gpath = path_query.sub( "_", group )
    if not os.path.isdir( gpath ) : os.mkdir( gpath )


    with requests.get( url ) as res:
        soup = BeautifulSoup( res.content, "html.parser" )
        scripts = soup.find_all("script")
        for scripts_index in range( 3, len( scripts ) ) :
            if scripts[ scripts_index ].has_attr("data-tralbum"):
                TralbumData = scripts[ scripts_index ]["data-tralbum"]
                break
            else:
                TralbumData = ""
            if len( TralbumData ) > 0 : break
        
    try:
        j = json.loads( TralbumData )
        if j:
            artist = "anonimous"
            if j["artist"] : artist = j["artist"]
            path = gpath + "/" + path_query.sub( "_", artist )
            if not os.path.isdir( path ) : os.mkdir( path )
            
            album = "no title"
            if j["packages"]:
                if j["packages"][0]["album_title"] : album = j["packages"][0]["album_title"]
            else:
                if j["current"] and j["current"]["title"] : album = j["current"]["title"]

            out_dir = path + "/" + path_query.sub( "_", album )
            if not os.path.isdir( out_dir ) : os.mkdir( out_dir )

            for t in j["trackinfo"]:
                track_num = 0
                if t['track_num'] : track_num = t['track_num']
                out =  out_dir + "/" + path_query.sub( "_", "{0:02d}_".format( track_num ) + t['title'] + ".mp3" )
                if not os.path.exists( out ):
                    if t['file']:
                        print( "Downloading ... : " + out )
                        mp3_url = t['file']['mp3-128']
                        with requests.get( mp3_url ) as res:
                            with open( out, 'wb' ) as of:
                                of.write( res.content )

    except Exception as e:
        print ( e )
        print ("JSON Decode error")
        print ( url )
        print ( scripts[ scripts_index ]   )


def album_download( url ):
    with requests.get( url ) as res:
        for l in res.content.splitlines() :
            l = l.decode()
            m = track_href.search( l )
            if m:
                if m.group( 1 ).count('?') == 0:
                    a = url.split( '/' )
                    print( a[0] + '//' + a[2] + m.group( 1 ) )
                    download( a[0] + '//' + a[2] + m.group( 1 ) )
        
if __name__ == '__main__':

    for url in os.sys.argv[ 1: ]:
        if track_searcher.search( url ) :
            download( url )
        else:
            with requests.get( url ) as res:
                for l in res.content.splitlines() :
                    l = l.decode()
                    m = album_href.search( l )
                    if m:
                        if m.group( 1 ).count('?') == 0:
                            a = url.split( '/' )
                            print( a[0] + '//' + a[2] + m.group( 1 ) )
                            album_download( a[0] + '//' + a[2] + m.group( 1 ) )
                   
