class AddVersionCreatedAt < ActiveRecord::Migration
  def self.up
    add_column :items, :version_created_at, :datetime
    ActiveRecord::Base.connection().execute "update items set version_created_at = updated_at"
  end

  def self.down
    remove_column :items, :version_created_at
  end
end