class AddPermalinks < ActiveRecord::Migration
  def self.up
    add_column :users, :permalink, :string
    add_column :items, :permalink, :string
    add_column :tags, :permalink, :string
  end

  def self.down
    remove_column :users, :permalink
    remove_column :items, :permalink
    remove_column :tags, :permalink
  end
end
