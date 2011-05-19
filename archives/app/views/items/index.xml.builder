xml.instruct!

xml.rss "version" => "2.0", "xmlns:dc" => "http://purl.org/dc/elements/1.1/" do
	xml.channel do
		xml.title			"Simplici7y"
		xml.link			items_url
		xml.pubDate			CGI.rfc1123_date @items.first.updated_at if @items.any?
		xml.description		"RSS Feed of new and updated files on Simplici7y"

		@items.each do |item|
			if item != nil && item.find_version != nil
				xml.item do
					xml.title       "#{item.name + ' ' + item.find_version.name}"
					xml.author      item.user.login
					xml.link        "#{item_url(item)}"
					xml.description item.mark_body
					xml.pubDate     CGI.rfc1123_date item.updated_at
				end
			end
		end
	end
end
