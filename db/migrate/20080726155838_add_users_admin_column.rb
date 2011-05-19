class AddUsersAdminColumn < ActiveRecord::Migration
  def self.up
    add_column :users, :admin, :integer, :null => false, :default => 0
  end

  def self.down
    remove_column :users, :admin
  end
end
