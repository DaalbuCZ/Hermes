import React, { useState } from "react";
import { Combobox } from "@shadcn/ui";

const ProfileCombobox = ({ profiles, onChange }) => {
  const [selectedProfile, setSelectedProfile] = useState(null);

  const handleChange = (profile) => {
    setSelectedProfile(profile);
    if (onChange) {
      onChange(profile);
    }
  };

  return (
    <Combobox
      value={selectedProfile}
      onChange={handleChange}
      options={profiles.map((profile) => ({
        value: profile.id,
        label: `${profile.name} ${profile.surname}`,
      }))}
      placeholder="Select Profile"
    />
  );
};

export default ProfileCombobox;
