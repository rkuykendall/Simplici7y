xml.instruct!

xml.rss "version" => "2.0", "xmlns:dc" => "http://purl.org/dc/elements/1.1/" do
	xml.channel do
		xml.title			"Simplici7y"
		xml.link			items_url
		xml.pubDate			CGI.rfc1123_date @items.first.updated_at if @items.any?
		xml.description		"S7 Files"

		@items.each do |item|
			if item != nil && item.find_version != nil
				xml.item do
					xml.title       "#{clean(item.name) + ' ' + clean(item.find_version.name)}"
					xml.author      clean(item.user.login)
					xml.link        "#{item_url(item)}"
					xml.description format(item.body)
					xml.pubDate     CGI.rfc1123_date item.updated_at
				end
			end
		end
	end
end
