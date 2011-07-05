class AddUserCountCaches < ActiveRecord::Migration
  def self.up
    add_column :users, :items_count, :integer, :default => 0
    add_column :users, :reviews_count, :integer, :default => 0

    User.reset_column_information

    User.find(:all).each do |u|
      # This command will fail to write if the column is identified as a counter cache.
      # Remove the counter cache => true from the review model before running.
      # For some reason, items works just fine.
      u.update_attribute :reviews_count, Review.find(:all, :conditions => [ "user_id = ?", u.id ]).length
      u.update_attribute :items_count, Item.find(:all, :conditions => [ "versions_count > 0 AND user_id = ?", u.id ]).length
    end
  end

  def self.down
    remove_column :users, :items_count
    remove_column :users, :reviews_count
  end
end