class AddLinks < ActiveRecord::Migration
  def self.up
    add_column :versions, :link, :string
  end

  def self.down
    remove_column :versions, :link
  end
end
