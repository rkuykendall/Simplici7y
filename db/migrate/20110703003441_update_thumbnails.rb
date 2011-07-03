class UpdateThumbnails < ActiveRecord::Migration
  def self.up
    Screenshot.find(:all).each do |s|
        s.file = File.open(s.file)
        s.save
        puts "Another image updated."
    end
  end

  def self.down
    # Not Applicable
  end
end
