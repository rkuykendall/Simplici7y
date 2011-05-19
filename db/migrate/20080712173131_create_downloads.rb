class CreateDownloads < ActiveRecord::Migration
  def self.up
    create_table :downloads do |t|
      t.integer :user_id
      t.integer :version_id
      t.integer :item_id

      t.timestamps
    end
  end

  def self.down
    drop_table :downloads
  end
end
