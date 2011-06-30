class DownloadTimeCounters < ActiveRecord::Migration
  def self.up
      add_column :items, :downloads_day_count, :integer, :null => false, :default => 0
      add_column :items, :downloads_week_count, :integer, :null => false, :default => 0
      add_column :items, :downloads_month_count, :integer, :null => false, :default => 0      
  end

  def self.down
    remove_column :items, :downloads_day_count
    remove_column :items, :downloads_week_count
    remove_column :items, :downloads_month_count
  end
end
