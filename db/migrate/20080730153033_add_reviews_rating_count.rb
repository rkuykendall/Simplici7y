class AddReviewsRatingCount < ActiveRecord::Migration
  def self.up
    add_column :items, :ratings_count, :float, :default => 0.0
    add_column :items, :ratings_weighted_count, :float, :default => 0.0

    for item in Item.find(:all)
      total = 0.0
      average = 0.0
      weighted = 0.0
      count = item.reviews.count.to_f

      if count > 0
        for review in item.reviews
          total += review.rating
        end

        average = total / count
        weighted = average + ( average - 2.5 ) * ( count / 10.0 )
      end

      Item.reset_column_information
      item.update_attributes(:ratings_count => average, :ratings_weighted_count => weighted)
    end
  end

  def self.down
    remove_column :items, :ratings_count
    remove_column :items, :ratings_weighted_count
  end
end