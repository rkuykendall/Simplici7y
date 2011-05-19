class DownloadCaches < ActiveRecord::Migration
  def self.up
    add_column :items, :downloads_count, :integer, :null => false, :default => 0
    add_column :items, :reviews_count, :integer, :null => false, :default => 0
    add_column :versions, :downloads_count, :integer, :null => false, :default => 0
  end

  def self.down
    remove_column :items, :downloads_count
    remove_column :items, :reviews_count
    remove_column :versions, :downloads_count
  end
end