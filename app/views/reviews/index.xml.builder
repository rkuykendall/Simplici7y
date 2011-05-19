xml.instruct!

xml.rss "version" => "2.0", "xmlns:dc" => "http://purl.org/dc/elements/1.1/" do
	xml.channel do
		xml.title			"S7 Reviews"
		xml.link			reviews_url
		xml.pubDate			CGI.rfc1123_date @reviews.first.created_at if @reviews.any?
		xml.description		"S7 Reviews"

		@reviews.each do |review|
			if review.item != nil && review.item.find_version != nil && review.user != nil
				xml.item do
					xml.title			"#{clean(review.title)} ( #{clean(review.item.name)} #{clean(review.item.find_version.name)} )"
					xml.author			review.user.login
					xml.link			"#{item_url review.item}"
					xml.description		format(review.body)
					xml.pubDate			CGI.rfc1123_date review.created_at
				end
			end
		end
	end
end
