class CreateReviews < ActiveRecord::Migration
  def self.up
    create_table :reviews do |t|
      t.integer :item_id
      t.integer :version_id
      t.integer :user_id
      t.string :title
      t.text :body
      t.integer :rating

      t.timestamps
    end
  end

  def self.down
    drop_table :reviews
  end
end
