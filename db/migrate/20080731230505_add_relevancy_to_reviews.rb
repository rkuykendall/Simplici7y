class AddRelevancyToReviews < ActiveRecord::Migration
  def self.up
    add_column :reviews, :relevancy, :integer, :null => false, :default => 0
    Review.reset_column_information
    
    for item in Item.find(:all)
      
      #--------------------[ Update Review Relevancy ]--------------------#
      
      reviews = item.reviews.find(:all, :order => 'created_at DESC')
      version = item.find_version

      reviews.each_with_index do |review, index|
        unless review.relevancy_changed?
          review.relevancy = 0
          review.relevancy = 1 if review.version_id != version.id
          review.relevancy = 2 if review.user_id == item.user_id
          (index+1...reviews.size).each do |r|
            reviews[r].relevancy = 2 if reviews[r].user_id == review.user_id
          end
        end

      end
      reviews.each(&:save!)
      
      #--------------------[ Update Ratings Caches ]--------------------#
      
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
    remove_column :reviews, :relevancy
  end
end