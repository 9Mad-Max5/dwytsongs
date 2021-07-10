#!/usr/bin/python3

import zipfile
from os import makedirs
from requests import get
from spotipy import oauth2
from mutagen.id3 import ID3, APIC
from mutagen.easyid3 import EasyID3
from collections import OrderedDict

header = {
    "Accept-Language": "en-US,en;q=0.5"
}


def generate_token():
    return oauth2.SpotifyClientCredentials(
        client_id="c6b23f1e91f84b6a9361de16aba0ae17",
        client_secret="237e355acaa24636abc79f1a089e6204"
    ).get_access_token()


def request(url, control=False):
    try:
        thing = get(url, headers=header)
    except:
        thing = get(url, headers=header)

    if control:
        try:
            if thing.json()['error']['message'] == "no data":
                raise exceptions.NoDataApi("No data avalaible :(")
        except KeyError:
            pass

        try:
            if thing.json()['error']['message'] == "Quota limit exceeded":
                raise exceptions.QuotaExceeded(
                    "Too much requests limit yourself")
        except KeyError:
            pass

        try:
            if thing.json()['error']:
                raise exceptions.InvalidLink("Invalid link ;)")
        except KeyError:
            pass

    return thing


def create_zip(zip_name, nams):
    z = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)

    for a in nams:
        b = a.split("/")[-1]

        try:
            z.write(a, b)
        except FileNotFoundError:
            pass

    z.close()


def artist_sort(array):
    if len(array) > 1:
        for a in array:
            for b in array:
                if a in b and a != b:
                    array.remove(b)

    artists = ", ".join(
        OrderedDict.fromkeys(array)
    )

    return artists


def check_dir(directory):
    try:
        makedirs(directory)
    except FileExistsError:
        pass


def var_excape(string):
    string = (
        string
        .replace("\\", "")
        .replace("/", "")
        .replace(":", "")
        .replace("*", "")
        .replace("?", "")
        .replace('"', "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
    )

    return string


def write_tags(song, data):
    tag = EasyID3(song)
    tag.delete()
    tag['artist'] = data['artist']
    tag['title'] = data['music']
    tag['date'] = data['year']
    tag['album'] = data['album']
    tag['tracknumber'] = data['tracknum']
    tag['discnumber'] = data['discnum']
    tag['genre'] = data['genre']
    tag['albumartist'] = data['ar_album']
    tag['bpm'] = data['bpm']
    tag['length'] = data['duration']
    tag['organization'] = data['label']
    tag['isrc'] = data['isrc']
    tag['replaygain_*_gain'] = data['gain']
    tag.save(v2_version=3)
    audio = ID3(song)

    audio['APIC'] = APIC(
        encoding=3,
        mime="image/jpeg",
        type=3,
        desc=u"Cover",
        data=data['image']
    )

    audio.save()


def create_naming(datas, output, plexnaming, humannaming, album):
    # Plex friendly structure
    if plexnaming is True:
        if datas['ar_album'] == "Various Artists":
            datas['ar_album'] = datas['artist']

        datas['tracknum'].zfill(2)

        directory = (
            "%s/%s/%s/"
            % (
                output,
                datas['ar_album'],
                album
            )
        )

        name = (
            "%s%s - %s"
            % (
                directory,
                datas['tracknum'],
                datas['music']
            )
        )

    # Mad-Max A more useable humandreadable Structure
    elif humannaming is True:
        # Mad-Max Replace Artist by using the album Artist. Get rid of Fearturings
        if datas['ar_album'] == "Various Artists":
            datas['ar_album'] = datas['artist']
        else:
            datas['artist'] = datas['ar_album']

        directory = (
            "%s/%s/"
            % (
                output,
                datas['ar_album']
            )
        )

        name = (
            "%s%s - %s"
            % (
                directory,
                datas['ar_album'],
                datas['music']
            )
        )
    else:
        # I didn't found the original code for the naming so this one is the fallback
        if datas['ar_album'] == "Various Artists":
            datas['ar_album'] = datas['artist']
        else:
            datas['artist'] = datas['ar_album']

        directory = (
            "%s/%s/"
            % (
                output,
                datas['ar_album']
            )
        )

        name = (
            "%s%s - %s"
            % (
                directory,
                datas['ar_album'],
                datas['music']
            )
        )
    return name, directory
