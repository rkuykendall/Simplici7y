class UpdateRatingsCaches < ActiveRecord::Migration
  def self.up
    for item in Item.find(:all)
      
      puts item.name
      
      #--------------------[ Update Rating Relevancy ]--------------------#
      
      reviews = item.reviews.find(:all, :order => 'created_at DESC')
      version = item.versions.reverse[0]

      reviews.each_with_index do |review, index|
          # Start at zero
          review.relevancy = 0

          # If it's an old version, bump it to 1
          review.relevancy = 1 if review.version_id != version.id

          # If there's a newer review, bump it to 3
          (0...index).each do |r|
            reviews[index].relevancy = 2 if reviews[r].user_id == review.user_id
          end

          # If it's by the owner, bump it to 2
          review.relevancy = 2 if review.user_id == item.user_id
      end
      reviews.each(&:save!)
      


      #--------------------[ Update Rating Counts ]--------------------#

      total = 0.0
      average = 0.0
      weighted = 0.0
      reviews = item.reviews.find(:all, :conditions => [ 'relevancy < 2' ])
      count = reviews.length.to_f

      if count > 0
        for review in reviews
          total += review.rating
        end

        average = total / count
        weighted = average + ( average - 2.5 ) * ( count / 10.0 )
      end

      item.update_attributes(:ratings_count => average, :ratings_weighted_count => weighted)

    end
  end

  def self.down
  end
end
