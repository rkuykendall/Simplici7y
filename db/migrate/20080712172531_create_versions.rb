class CreateVersions < ActiveRecord::Migration
  def self.up
    create_table :versions do |t|
      t.integer :item_id
      t.string :name
      t.string :file
      t.text :body

      t.timestamps
    end
  end

  def self.down
    drop_table :versions
  end
end
