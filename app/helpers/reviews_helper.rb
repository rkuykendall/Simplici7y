module ReviewsHelper
  def stars(rating)
    width = (rating * 25).to_i;
    s = %{ <ul class='star-rating'>
		    <li class='current-rating' style='width:#{width}px;'>Currently #{rating}/5 Stars.</li>
		</ul> }
  end
end
