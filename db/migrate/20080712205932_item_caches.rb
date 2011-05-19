class ItemCaches < ActiveRecord::Migration
  def self.up
    add_column :items, :screenshots_count, :integer, :null => false, :default => 0
    add_column :items, :versions_count, :integer, :null => false, :default => 0
  end

  def self.down
    remove_column :items, :screenshots_count
    remove_column :items, :versions_count
  end
end