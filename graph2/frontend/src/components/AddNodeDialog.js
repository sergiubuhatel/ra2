// src/components/AddNodeDialog.js
import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  List,
  ListItem,
  Button,
  InputAdornment,
} from "@mui/material";

export default function AddNodeDialog({
  open,
  onClose,
  onSubmit,
  newNodeTicker,
  setNewNodeTicker,
  selectedConnections,
  toggleConnection,
  handleWeightChange,
  existingNodes,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add New Node</DialogTitle>
      <DialogContent>
        <TextField
          label="Ticker / Name"
          value={newNodeTicker}
          onChange={(e) => setNewNodeTicker(e.target.value)}
          fullWidth
          margin="normal"
        />

        <p>Select connections and set weights:</p>
        <List style={{ maxHeight: 300, overflowY: "auto" }}>
          {existingNodes.map((existingNode) => {
            const isChecked = selectedConnections.hasOwnProperty(existingNode.id);
            return (
              <ListItem key={existingNode.id} dense>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={isChecked}
                      onChange={() => toggleConnection(existingNode.id)}
                    />
                  }
                  label={`${existingNode.label} (${existingNode.industry || "Unknown"})`}
                  style={{ flex: 1 }}
                />
                {isChecked && (
                  <TextField
                    type="number"
                    size="small"
                    inputProps={{ min: 0, step: 0.1 }}
                    value={selectedConnections[existingNode.id]}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      handleWeightChange(existingNode.id, isNaN(val) ? 0 : val);
                    }}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">Weight</InputAdornment>,
                    }}
                    style={{ width: 100 }}
                  />
                )}
              </ListItem>
            );
          })}
        </List>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={onSubmit}>
          Add Node
        </Button>
      </DialogActions>
    </Dialog>
  );
}
