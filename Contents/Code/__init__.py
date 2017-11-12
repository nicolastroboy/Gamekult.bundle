NAME = 'Gamekult'
ICON = 'icon-default.jpg'
ART = 'art-default.jpg'
FF = 1 # Family Filter, we default to 1 (meaning it is enabled)

####################################################################################################
def Start():

	Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	# Setup the default attributes for the ObjectContainer
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'List'
	ObjectContainer.art = R(ART)

	# Setup the default attributes for the other objects
	DirectoryObject.thumb = R(ICON)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON)
	NextPageObject.thumb = R(ICON)

	# Setup some basic things the plugin needs to know about
	HTTP.CacheTime = 1800

####################################################################################################
@handler('/video/gamekult', NAME, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()

	oc.add(DirectoryObject(key=Callback(GetVideoList, path="playlist/x1ucn3/videos", sort="recent", title2="Emission"), title="Emission"))
	oc.add(DirectoryObject(key=Callback(GetVideoList, path="playlist/x3u988/videos", sort="recent", title2="Gaijin Dash"), title="Gaijin Dash"))

	return oc

####################################################################################################
@route("/video/gamekult/getvideolist", limit=int, page=int)
def GetVideoList(path="videos", filters=None, sort="recent", limit=25, page=1, title2="Videos", search=None):

	oc = ObjectContainer(title2=title2)

	# Callbacks turn "" into None, which we don't want -- use None and revert it to "" as required
	if filters == None:
		filters = ""

	fields = "title,description,thumbnail_large_url,rating,url,duration,created_time,views_total"
	full_url = "https://api.dailymotion.com/%s?sort=%s&filters=%s&limit=%i&page=%i&fields=%s&family_filter=%i" % (path, sort, filters, limit, page, fields, FF)

	if search != None:
		full_url = "%s&search=%s" % (full_url, search) # only add search if applicable, API doesn't like a NULL search request

	data = JSON.ObjectFromURL(full_url)

	for video in data['list']:
		title = video['title']
		url = video['url']
		duration = video['duration']*1000 # worst case duration is 0 so we get 0

		try:
			views = "\n\nViews: %i" % video["views_total"]
		except:
			views = ""

		try:
			summary = String.StripTags(video['description'].replace("<br />", "\n"))
			summary = summary.strip()
		except:
			summary = None

		try:
			thumb_url = video['thumbnail_large_url']
		except:
			thumb_url = ""

		try:
			rating = float(video['rating']*2)
		except:
			rating = None

		try:
			originally_available_at = Datetime.FromTimestamp(video['created_time'])
		except:
			originally_available_at = None

		oc.add(
			VideoClipObject(
				url = url,
				title = title,
				summary = summary,
				duration = duration,
				rating = rating,
				originally_available_at = originally_available_at,
				thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
			)
		)

	# pagination
	if data['has_more']:
		oc.add(NextPageObject(key=Callback(GetVideoList, path=path, filters=filters, sort=sort, limit=limit, page=int(page+1), title2=title2, search=search), title="Suite..."))

	return oc
